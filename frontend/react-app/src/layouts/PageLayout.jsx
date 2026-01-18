import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";

export default function PageLayout() {

  return (

    <div className="h-screen flex flex-col bg-white text-black font-anonymous-pro overflow-hidden">
      <Navbar />
      <div className="flex-1 w-full relative">
        <Outlet />
      </div>
    </div>
  );
}