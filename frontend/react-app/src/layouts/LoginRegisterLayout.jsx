import { Outlet } from "react-router-dom";

export default function LoginRegisterLayout() {
  return (
    <div className="min-h-screen bg-[#f3f3f3] text-black font-anonymous-pro">
      <Outlet />
    </div>
  );
}