import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', 'ec7'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '25d'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'ee4'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'dc4'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '3e2'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', 'c81'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '3fd'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '526'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '174'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', '828'),
            routes: [
              {
                path: '/docs/capstone/',
                component: ComponentCreator('/docs/capstone/', 'fd4'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/capstone/architecture',
                component: ComponentCreator('/docs/capstone/architecture', '17a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/capstone/hardware-setup',
                component: ComponentCreator('/docs/capstone/hardware-setup', '54b'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/capstone/implementation',
                component: ComponentCreator('/docs/capstone/implementation', 'b06'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/capstone/integration-guide',
                component: ComponentCreator('/docs/capstone/integration-guide', '4f6'),
                exact: true
              },
              {
                path: '/docs/environment-configuration',
                component: ComponentCreator('/docs/environment-configuration', '7a2'),
                exact: true
              },
              {
                path: '/docs/infrastructure/cost-performance',
                component: ComponentCreator('/docs/infrastructure/cost-performance', '9c0'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/infrastructure/hardware-requirements',
                component: ComponentCreator('/docs/infrastructure/hardware-requirements', '761'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/infrastructure/onprem-vs-cloud',
                component: ComponentCreator('/docs/infrastructure/onprem-vs-cloud', '028'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', 'aed'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/modules/module-1-ros/',
                component: ComponentCreator('/docs/modules/module-1-ros/', 'cb8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/modules/module-1-ros/exercises/basic-pubsub-exercise',
                component: ComponentCreator('/docs/modules/module-1-ros/exercises/basic-pubsub-exercise', '437'),
                exact: true
              },
              {
                path: '/docs/modules/module-1-ros/ros-nervous-system',
                component: ComponentCreator('/docs/modules/module-1-ros/ros-nervous-system', '925'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/modules/module-2-digital-twins/',
                component: ComponentCreator('/docs/modules/module-2-digital-twins/', '8c7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/modules/module-2-digital-twins/gazebo-simulations',
                component: ComponentCreator('/docs/modules/module-2-digital-twins/gazebo-simulations', 'c05'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/modules/module-2-digital-twins/unity-integration',
                component: ComponentCreator('/docs/modules/module-2-digital-twins/unity-integration', '685'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/modules/module-3-isaac/',
                component: ComponentCreator('/docs/modules/module-3-isaac/', 'eca'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/modules/module-3-isaac/exercises/',
                component: ComponentCreator('/docs/modules/module-3-isaac/exercises/', '7d0'),
                exact: true
              },
              {
                path: '/docs/modules/module-3-isaac/isaac-ros',
                component: ComponentCreator('/docs/modules/module-3-isaac/isaac-ros', '346'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/modules/module-3-isaac/isaac-sim',
                component: ComponentCreator('/docs/modules/module-3-isaac/isaac-sim', 'ef9'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/modules/module-4-vla/',
                component: ComponentCreator('/docs/modules/module-4-vla/', '326'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/modules/module-4-vla/conversational-robots',
                component: ComponentCreator('/docs/modules/module-4-vla/conversational-robots', 'ac5'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/modules/module-4-vla/exercises/',
                component: ComponentCreator('/docs/modules/module-4-vla/exercises/', 'e04'),
                exact: true
              },
              {
                path: '/docs/modules/module-4-vla/vision-language-action',
                component: ComponentCreator('/docs/modules/module-4-vla/vision-language-action', '584'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/overview/physical-ai-concepts',
                component: ComponentCreator('/docs/overview/physical-ai-concepts', 'b75'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/overview/quarter-overview',
                component: ComponentCreator('/docs/overview/quarter-overview', 'e75'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', '0fc'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
