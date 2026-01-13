import { Outlet } from "react-router-dom";

export default function LoginRegisterLayout() {

  {/*
    <div className="min-h-screen bg-[#f3f3f3] text-black font-anonymous-pro">
      <Outlet />
    </div>
    */}

  return (
    <div className="min-h-screen bg-white text-black font-anonymous-pro">
      <Outlet />
    </div>
  );
}