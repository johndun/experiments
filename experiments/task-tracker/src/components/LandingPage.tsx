import { Link } from 'react-router-dom';
import styles from './LandingPage.module.css';

export default function LandingPage() {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>Task Tracker</h1>
        <p className={styles.subtitle}>
          Organize your tasks and boost your productivity
        </p>
      </header>

      <main className={styles.main}>
        <section className={styles.features}>
          <div className={styles.feature}>
            <h3>📝 Create Tasks</h3>
            <p>Add and organize your daily tasks with ease</p>
          </div>
          <div className={styles.feature}>
            <h3>✅ Track Progress</h3>
            <p>Mark tasks as complete and monitor your progress</p>
          </div>
          <div className={styles.feature}>
            <h3>🎯 Stay Focused</h3>
            <p>Prioritize tasks and maintain focus on what matters</p>
          </div>
        </section>

        <div className={styles.actions}>
          <button className={styles.primaryButton}>Get Started</button>
          <Link to="/about" className={styles.secondaryButton}>
            Learn More
          </Link>
        </div>
      </main>

      <footer className={styles.footer}>
        <p>Built with React, TypeScript, and Vite</p>
      </footer>
    </div>
  );
}
