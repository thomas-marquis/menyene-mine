import { useAppSelector } from '../../store';
import './Home.module.css';

export const HomePage = () => {
  const { isAuthenticated, user } = useAppSelector((state) => state.auth);

  return (
    <div className="home-container">
      <h1>Welcome to Menyene Mine</h1>
      {isAuthenticated ? (
        <div>
          <p>Hello, {user?.name || 'User'}!</p>
          <p>You are logged in.</p>
        </div>
      ) : (
        <div>
          <p>Please log in to continue.</p>
        </div>
      )}
    </div>
  );
};
