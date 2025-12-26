// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Overview',
      items: [
        'overview/quarter-overview',
        'overview/physical-ai-concepts'
      ],
    },
    {
      type: 'category',
      label: 'Module 1: ROS 2 Nervous System',
      items: [
        'modules/module-1-ros/index',
        'modules/module-1-ros/ros-nervous-system'
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Digital Twins',
      items: [
        'modules/module-2-digital-twins/index',
        'modules/module-2-digital-twins/gazebo-simulations',
        'modules/module-2-digital-twins/unity-integration'
      ],
    },
    {
      type: 'category',
      label: 'Module 3: NVIDIA Isaac',
      items: [
        'modules/module-3-isaac/index',
        'modules/module-3-isaac/isaac-sim',
        'modules/module-3-isaac/isaac-ros'
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Vision-Language-Action',
      items: [
        'modules/module-4-vla/index',
        'modules/module-4-vla/vision-language-action',
        'modules/module-4-vla/conversational-robots'
      ],
    },
    {
      type: 'category',
      label: 'Capstone Project',
      items: [
        'capstone/index',
        'capstone/architecture',
        'capstone/implementation',
        'capstone/hardware-setup'
      ],
    },
    {
      type: 'category',
      label: 'Infrastructure',
      items: [
        'infrastructure/hardware-requirements',
        'infrastructure/onprem-vs-cloud',
        'infrastructure/cost-performance'
      ],
    },
  ],
};

module.exports = sidebars;