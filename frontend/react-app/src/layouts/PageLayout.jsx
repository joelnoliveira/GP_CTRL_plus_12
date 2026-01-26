import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";

export default function PageLayout() {

  return (

    <div className="min-h-screen flex flex-col bg-white text-black font-anonymous-pro">
      <Navbar />
      <div className="flex-1 flex w-full relative">
        <Outlet />
      </div>
    </div>
  );
}