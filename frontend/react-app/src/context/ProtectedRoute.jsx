import { Navigate } from "react-router-dom";
import { useAuth } from "./AuthContext";

const ProtectedRoute = ({ children }) => {
    const { isLoggedIn } = useAuth();

    // Assuming AuthContext handles initial loading state correctly, 
    // otherwise might need to add loading check here if auth state is async.
    // For now, based on useAuth simplified usage, we check isLoggedIn directly.

    if (!isLoggedIn) {
        return <Navigate to="/login" replace />;
    }

    return children;
};

export default ProtectedRoute;
