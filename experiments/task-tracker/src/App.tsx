import { Routes, Route } from 'react-router-dom';
import LandingPage from './components/LandingPage';
import styles from './App.module.css';

function App() {
  return (
    <div className={styles.root}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
      </Routes>
    </div>
  );
}

export default App;
