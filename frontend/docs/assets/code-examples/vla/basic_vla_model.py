#!/usr/bin/env python3
"""
Basic Vision-Language-Action Model

This script demonstrates a simple implementation of a Vision-Language-Action model.
"""

import torch
import torch.nn as nn
import torchvision.models as models
from transformers import AutoTokenizer, AutoModel
import numpy as np


class VisionEncoder(nn.Module):
    """
    Vision encoder using a pre-trained CNN
    """
    def __init__(self, pretrained=True):
        super().__init__()
        # Use ResNet as the backbone
        self.backbone = models.resnet18(pretrained=pretrained)

        # Remove the final classification layer
        self.features = nn.Sequential(*list(self.backbone.children())[:-1])

        # Add a projection layer to match desired feature dimension
        self.projection = nn.Linear(512, 256)  # ResNet18 outputs 512-dim features

    def forward(self, images):
        # Extract features
        features = self.features(images)

        # Flatten and project
        features = torch.flatten(features, 1)
        features = self.projection(features)

        return features


class LanguageEncoder(nn.Module):
    """
    Language encoder using a transformer model
    """
    def __init__(self, model_name='bert-base-uncased'):
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

        # Add special tokens if they don't exist
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Projection layer to match vision feature dimension
        self.projection = nn.Linear(self.model.config.hidden_size, 256)

    def forward(self, text_commands):
        # Tokenize input
        inputs = self.tokenizer(
            text_commands,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=128
        )

        # Get embeddings
        outputs = self.model(**inputs)

        # Use [CLS] token embedding as sentence representation
        sentence_embedding = outputs.last_hidden_state[:, 0, :]

        # Project to desired dimension
        projected_embedding = self.projection(sentence_embedding)

        return projected_embedding


class CrossAttentionFusion(nn.Module):
    """
    Cross-attention mechanism to fuse vision and language features
    """
    def __init__(self, feature_dim=256, num_heads=8):
        super().__init__()
        self.feature_dim = feature_dim
        self.num_heads = num_heads

        # Multi-head attention for cross-modal interaction
        self.attention = nn.MultiheadAttention(
            embed_dim=feature_dim,
            num_heads=num_heads,
            batch_first=True
        )

        # Layer normalization
        self.norm_vision = nn.LayerNorm(feature_dim)
        self.norm_language = nn.LayerNorm(feature_dim)

        # Feed-forward network
        self.ffn = nn.Sequential(
            nn.Linear(feature_dim, feature_dim * 4),
            nn.ReLU(),
            nn.Linear(feature_dim * 4, feature_dim)
        )

    def forward(self, vision_features, language_features):
        # Reshape for attention (batch_size, seq_len, feature_dim)
        vision_features = vision_features.unsqueeze(1)  # Add sequence dimension
        language_features = language_features.unsqueeze(1)

        # Cross-attention: vision attending to language
        vision_attended, _ = self.attention(
            vision_features, language_features, language_features
        )

        # Cross-attention: language attending to vision
        language_attended, _ = self.attention(
            language_features, vision_features, vision_features
        )

        # Residual connections and normalization
        vision_fused = self.norm_vision(vision_features + vision_attended)
        language_fused = self.norm_language(language_features + language_attended)

        # Combine the fused features
        combined = vision_fused + language_fused

        # Apply feed-forward network
        output = self.ffn(combined.squeeze(1))

        return output


class ActionDecoder(nn.Module):
    """
    Action decoder to generate robot actions from fused features
    """
    def __init__(self, input_dim=256, action_dim=6):
        super().__init__()
        self.action_dim = action_dim

        # Simple MLP for action generation
        self.network = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, action_dim)
        )

        # Initialize weights
        self._init_weights()

    def _init_weights(self):
        """Initialize weights for better convergence"""
        for m in self.network:
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.constant_(m.bias, 0)

    def forward(self, fused_features):
        # Generate action
        action = self.network(fused_features)

        # Apply tanh to bound the output
        action = torch.tanh(action)

        return action


class VisionLanguageActionModel(nn.Module):
    """
    Complete Vision-Language-Action model
    """
    def __init__(self):
        super().__init__()

        self.vision_encoder = VisionEncoder()
        self.language_encoder = LanguageEncoder()
        self.fusion_module = CrossAttentionFusion()
        self.action_decoder = ActionDecoder()

    def forward(self, images, text_commands):
        # Encode visual input
        visual_features = self.vision_encoder(images)

        # Encode language input
        language_features = self.language_encoder(text_commands)

        # Fuse multimodal features
        fused_features = self.fusion_module(visual_features, language_features)

        # Generate actions
        actions = self.action_decoder(fused_features)

        return actions

    def predict_action(self, image, command):
        """
        Convenience method for single prediction
        """
        self.eval()
        with torch.no_grad():
            # Add batch dimension
            image_batch = image.unsqueeze(0)
            command_batch = [command]

            # Forward pass
            action = self(image_batch, command_batch)

            # Remove batch dimension
            return action.squeeze(0)


def create_sample_data():
    """
    Create sample data for testing the VLA model
    """
    # Create sample images (batch_size=2, channels=3, height=224, width=224)
    sample_images = torch.randn(2, 3, 224, 224)

    # Create sample text commands
    sample_commands = [
        "pick up the red object",
        "move to the blue box"
    ]

    # Create sample actions (for training)
    sample_actions = torch.randn(2, 6)  # 6-dof actions

    return sample_images, sample_commands, sample_actions


def train_vla_model():
    """
    Example training loop for the VLA model
    """
    # Initialize model
    model = VisionLanguageActionModel()

    # Create sample data
    images, commands, actions = create_sample_data()

    # Define loss function and optimizer
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

    # Training loop
    model.train()
    for epoch in range(10):
        optimizer.zero_grad()

        # Forward pass
        predicted_actions = model(images, commands)

        # Calculate loss
        loss = criterion(predicted_actions, actions)

        # Backward pass
        loss.backward()
        optimizer.step()

        print(f'Epoch {epoch}, Loss: {loss.item():.4f}')

    return model


def main():
    """
    Main function to demonstrate the VLA model
    """
    print("Creating Vision-Language-Action model...")

    # Create the model
    vla_model = VisionLanguageActionModel()

    print("Model created successfully!")
    print(f"Total parameters: {sum(p.numel() for p in vla_model.parameters()):,}")

    # Create sample input
    sample_image = torch.randn(1, 3, 224, 224)  # Single image
    sample_command = ["pick up the object"]

    # Test the model
    print("\nTesting model with sample input...")
    with torch.no_grad():
        output = vla_model(sample_image, sample_command)
        print(f"Model output shape: {output.shape}")
        print(f"Sample output: {output[0].tolist()}")

    # Example of using the prediction method
    action = vla_model.predict_action(sample_image[0], "move forward")
    print(f"Predicted action: {action.tolist()}")

    # Train the model (example)
    print("\nTraining model (example)...")
    trained_model = train_vla_model()

    print("VLA model demonstration completed!")


if __name__ == "__main__":
    main()