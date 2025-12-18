import { React, useState } from "react";
import { Link } from "react-router-dom";
import FormWrapper from "../components/FormWrapper";
import TextField from "../components/TextField";
import Button from "../components/Button.jsx"
import Logo from "../components/Logo";

export default function Register() {
  	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [confirm_password, setConfirmPassword] = useState("");
	const [errors, setErrors] = useState({});
	const [touched, setTouched] = useState({});

	const validateInputs = () => {
		const newErrors = {};

		/*
		Falta erros de email já em uso,
		mas penso que esta parte dos erros vai ter de ser refeita
		porque eles no backend já verficam isto tudo (não sei se é melhor aqui ou lá tho)
		*/

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
		}else if (password!=confirm_password){
			newErrors.confirm_password = "Passwords do not match";
			newErrors.password = "Passwords do not match";
		}

		return newErrors;
		};

	const handleSubmit = (e) => {
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
		email,
		password,
		confirm_password,
		};

		console.log("Login payload:", payload);

		// call API 
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