import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Explore the Book
          </Link>
          <Link
            className="button button--primary button--lg"
            to="/docs/intro">
            Start Learning
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Physical AI & Humanoid Robotics`}
      description="A comprehensive guide to embodied intelligence and humanoid robotics">
      <HomepageHeader />
      <main>
        <section className={styles.section}>
          <div className="container">
            <div className="row">
              <div className="col col--12 text--center">
                <h2 className={styles.sectionTitle}>The Future of Robotics</h2>
                <p className={styles.sectionDescription}>
                  Welcome to the comprehensive guide on Physical AI and Humanoid Robotics.
                  This book explores the cutting-edge intersection of artificial intelligence and physical systems,
                  where machines learn to understand, interact with, and manipulate the physical world.
                </p>
              </div>
            </div>

            <div className="row margin-top--lg">
              <div className="col col--4">
                <div className={styles.featureCard}>
                  <h3>Physical AI</h3>
                  <p>
                    Discover how AI systems can understand and interact with the physical world
                    through embodied intelligence and sensorimotor learning.
                  </p>
                </div>
              </div>
              <div className="col col--4">
                <div className={styles.featureCard}>
                  <h3>Humanoid Robotics</h3>
                  <p>
                    Explore the design, control, and intelligence of robots with human-like
                    characteristics and behaviors for complex real-world tasks.
                  </p>
                </div>
              </div>
              <div className="col col--4">
                <div className={styles.featureCard}>
                  <h3>Advanced Systems</h3>
                  <p>
                    Learn about ROS 2, Digital Twins, NVIDIA Isaac, and Vision-Language-Action
                    models for next-generation robotic systems.
                  </p>
                </div>
              </div>
            </div>

            <div className="row margin-top--lg">
              <div className="col col--12 text--center">
                <div className={styles.chatWidgetCallout}>
                  <h3>Need Help? Ask Our AI Assistant</h3>
                  <p>
                    Use the floating chat widget to ask questions about the book content.
                    Our AI assistant is trained on the entire book and can provide detailed answers.
                  </p>
                  <Link
                    className="button button--outline button--secondary button--md"
                    to="/docs/intro">
                    Start Exploring
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}