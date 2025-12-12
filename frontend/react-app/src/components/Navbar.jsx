import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <div className="flex items-center justify-between px-8 py-2 bg-red-300">
	  <Link to="/">
      	<img src="/logo_GP.png" className="w-24 h-24" alt="Logo" />
	  </Link>

      <div className="flex items-center space-x-6">
        <Link to="/register">
          <button className="px-8 py-3 bg-white border border-black rounded-md hover:bg-black hover:text-white">
            Register
          </button>
        </Link>

        <Link to="/login">
          <button className="px-8 py-3 bg-red-600 text-white rounded-md hover:bg-red-800">
            Login
          </button>
        </Link>
      </div>
    </div>
  );
}