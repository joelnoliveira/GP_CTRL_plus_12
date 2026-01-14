import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";

export default function PageLayout() {

  {/*<div className="min-h-screen bg-[#f3f3f3] text-black font-anonymous-pro">
      <Navbar />
      <Outlet />
    </div>*/}

  return (

    <div className="min-h-screen bg-white text-black font-anonymous-pro">
      <Navbar />
      <Outlet />
    </div>
  );
}