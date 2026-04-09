import { createContext, useContext } from 'react';

const AuthContext = createContext({
  user: null,
  isAuthenticated: false,
  isLoadingAuth: false,
  isLoadingPublicSettings: false,
  authError: null,
  appPublicSettings: null,
  logout: () => {},
  navigateToLogin: () => {},
  checkAppState: async () => {},
});

export function AuthProvider({ children }) {
  return (
    <AuthContext.Provider
      value={{
        user: null,
        isAuthenticated: false,
        isLoadingAuth: false,
        isLoadingPublicSettings: false,
        authError: null,
        appPublicSettings: null,
        logout: () => {},
        navigateToLogin: () => {},
        checkAppState: async () => {},
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
