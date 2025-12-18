import { React, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from '../context/AuthContext';
import FormWrapper from "../components/FormWrapper";
import TextField from "../components/TextField";
import Button from "../components/Button";
import Logo from "../components/Logo";

import "../styles/pages/login.css";

export default function Login() {

	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [errors, setErrors] = useState({});
	const [touched, setTouched] = useState({});

	const { login } = useAuth(); // From your AuthContext
	const navigate = useNavigate();

	const validateInputs = () => {
		const newErrors = {};

		if(!email) {
			newErrors.email = "Email is required";
		}else if (!/\S+@\S+\.\S+/.test(email)) {
			newErrors.email = "Invalid email format";
		}

		if(!password) {
			newErrors.password = "Password is required";
		}else if (password.length < 8) {
			newErrors.password = "Password must be at least 8 characters";
		}

		return newErrors;
		};

	const handleSubmit = (e) => {
		e.preventDefault();

		setTouched({
			email: true,
			password: true,
		});

		const validationErrors = validateInputs();
		setErrors(validationErrors);

		if (Object.keys(validationErrors).length > 0) return;

		const payload = {
		email,
		password,
		};

		console.log("Login payload:", payload);

		// call API 

		const success = true; // Replace with actual API logic

		if (success) {
			login();
			navigate("/");
		}
	};

	return (
		<div className="login-page__wrapper">
			<div
			className="absolute left-0 bottom-0 w-2/5 h-3/5 bg-red-200 -z-2"
			style={{ clipPath: "polygon(0% 100%, 0% 0%, 100% 100%)" }}
			></div>
			<div className="login-page">
				<Link to="/">
					<Logo 
						size="large" 
					/>
				</Link>

				<div className="login__form relative z-0">
					<FormWrapper onSubmit={handleSubmit}>
						<TextField
							label="Email"
							type="email"
							value={email}
							onChange={(e) => setEmail(e.target.value)}
							onBlur={() => setTouched((t) => ({ ...t, email: true }))}
							placeholder="you@example.com"
							name="email"
							required={true}
							error={touched.email && errors.email}
							/>

						<TextField
							label="Password"
							type="password"
							value={password}
							onChange={(e) => setPassword(e.target.value)}
							onBlur={() => setTouched((t) => ({ ...t, password: true }))}
							placeholder="••••••••"
							name="password"
							required={true}
							error={touched.password && errors.password}
							/>

						<Button
							type="submit"
							variant="default"
							size="large"
							text="Login"
							styles="w-full"
						/>
					</FormWrapper>
				</div>

				<Link to="/register">
					<p className="login__signin-paragraph relative z-0">If you do not have an account - <span className="underline font-bold relative z-0">Create an account!</span>.</p>
				</Link>
			</div>
		</div>
	);
}