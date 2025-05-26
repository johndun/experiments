import { Routes, Route } from 'react-router-dom';
import styles from './App.module.css';

// Temporary home component - will be replaced with proper landing page component
function Home() {
  return (
    <div className={styles.root}>
      <h1>Task Tracker</h1>
      <p>Welcome to the Task Tracker application!</p>
      <p>React Router is now configured with basename: /experiments/task-tracker</p>
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
    </Routes>
  );
}

export default App;
