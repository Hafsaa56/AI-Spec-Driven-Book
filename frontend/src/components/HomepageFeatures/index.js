import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Physical AI',
    description: (
      <>
        Explore the fundamentals of Physical AI - the intersection of artificial intelligence and physical systems.
        Learn how AI can understand, interact with, and manipulate the physical world.
      </>
    ),
  },
  {
    title: 'Humanoid Robotics',
    description: (
      <>
        Discover the world of humanoid robotics, including locomotion, manipulation,
        and social interaction capabilities.
      </>
    ),
  },
  {
    title: 'Advanced Topics',
    description: (
      <>
        Dive into advanced topics including ROS 2, Digital Twins, NVIDIA Isaac,
        and Vision-Language-Action models.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}