import { Link } from "react-router-dom";

export default function Register() {
  return (
	<div>
		<div
        className="absolute left-0 bottom-0 w-2/5 h-3/5 bg-red-200 -z-2"
        style={{ clipPath: "polygon(0% 100%, 0% 0%, 100% 100%)" }}
		></div>
		<div className="flex py-12 justify-center w-screen h-screen">
			<Link to="/">
				<img src="/logo_GP.png" className="w-64 h-64" alt="Logo" />
			</Link>
		</div>
	</div>
  );
}