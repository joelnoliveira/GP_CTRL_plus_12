import { React, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import FormWrapper from "../components/FormWrapper";
import TextField from "../components/TextField";
import Button from "../components/Button.jsx"
import Logo from "../components/Logo";
import Toast from "../components/Toast";

export default function Register() {
  	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [confirm_password, setConfirmPassword] = useState("");
	const [errors, setErrors] = useState({});
	const [touched, setTouched] = useState({});
	const [toastConfig, setToastConfig] = useState(null);

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

		if(!confirm_password) {
			newErrors.confirm_password = "Password confirmation is required";
		}else if (confirm_password.length < 8) {
			newErrors.confirm_password = "Password confirmation must be at least 8 characters";
		}else if (password!==confirm_password){
			newErrors.confirm_password = "Passwords do not match";
			newErrors.password = "Passwords do not match";
		}

		return newErrors;
		};

	const processErrors = (error_message) => {
		const newErrors = {};

		if(error_message==="Database tables not reflected yet"){
			newErrors.showToast = { type: "error", message: "Internal Error." };
		} else if(error_message==="Email already registered"){
			newErrors.email = "Email already registered"
		} else{
			newErrors.showToast = { type: "error", message: "Register Error." };
		}
			
		return newErrors;
		};

	const handleSubmit = async (e) => {
		e.preventDefault();

		setTouched({
			email: true,
			password: true,
			confirm_password: true,
		});

		const validationErrors = validateInputs();
		setErrors(validationErrors);

		if (Object.keys(validationErrors).length > 0) return;

		const payload = {
		'email': email,
		'password': password,
		};

		console.log("Register payload:", payload);

		try {
			const response = await fetch("http://localhost:8000/auth/register", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(payload),
			});

			if (!response.ok) {
				const errorData = await response.json();
				throw new Error(errorData.detail || "Register failed");
			}
			
			console.log("Register success");
			navigate("/login");

		} catch (err) {
			console.error("API Error:", err.message);
			const backendErrors = processErrors(err.message);
			if (backendErrors.showToast) {
				setToastConfig(backendErrors.showToast);
				setTimeout(() => setToastConfig(null), 3000);
			}
			setErrors(backendErrors);
		}
	};

	return (
		<div className="login-page__wrapper">
			{/* Only render if toastConfig is not null */}
			{toastConfig && (
				<Toast
					icon_size="large"
					type={toastConfig.type}
					message={toastConfig.message}
					onClose={() => setToastConfig(null)} 
				/>
			)}
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

						<TextField
							label="Confirm Password"
							type="password"
							value={confirm_password}
							onChange={(e) => setConfirmPassword(e.target.value)}
							onBlur={() => setTouched((t) => ({ ...t, confirm_password: true }))}
							placeholder="••••••••"
							name="password"
							required={true}
							error={touched.confirm_password && errors.confirm_password}
							/>

						<Button
							type="submit"
							variant="default"
							size="large"
							text="Register"
							styles="w-full"
						/>
					</FormWrapper>
				</div>
			</div>
		</div>
	);
}