import { React, useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from '../context/AuthContext';
import ReCAPTCHA from "react-google-recaptcha";
import FormWrapper from "../components/FormWrapper";
import TextField from "../components/TextField";
import Button from "../components/Button";
import Logo from "../components/Logo";
import Toast from "../components/Toast";

import "../styles/pages/login.css";

export default function Login() {

	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [errors, setErrors] = useState({});
	const [touched, setTouched] = useState({});
	const [toastConfig, setToastConfig] = useState(null);

	const recaptchaRef = useRef();

	const { isLoggedIn, login } = useAuth(); // From your AuthContext
	const navigate = useNavigate();

	useEffect(() => {
	// console.log("Login sees isLoggedIn:", isLoggedIn);
	if (isLoggedIn) {
		navigate("/");
	}
	}, [isLoggedIn, navigate]);

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

	const processErrors = (error_message) => {
		const newErrors = {};

		if(error_message==="Database tables not reflected yet"){
			newErrors.showToast = { type: "error", message: "Internal Error." };
		} else if(error_message==="Invalid credentials"){
			newErrors.showToast = { type: "error", message: "Invalid credentials"};
		} else{
			newErrors.showToast = { type: "error", message: "Login Error." };
		}
			
		return newErrors;
		};

	const handleSubmit = async (e) => {
		e.preventDefault();

		const captchaToken = recaptchaRef.current.getValue();

		setTouched({
			email: true,
			password: true,
		});

		const validationErrors = validateInputs();
		setErrors(validationErrors);

		if (Object.keys(validationErrors).length > 0) return;

		if (!captchaToken) {
            setToastConfig({ type: "error", message: "Please complete the reCAPTCHA" });
            setTimeout(() => setToastConfig(null), 3000);
            return;
        }

		const payload = {
		'email': email,
		'password': password,
		'captcha_token': captchaToken,
		};

		// console.log("Login payload:", payload);


		try {
			const response = await fetch("http://localhost:8000/auth/login", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(payload),
			});

			if (!response.ok) {
				recaptchaRef.current.reset();
				const errorData = await response.json();
				throw new Error(errorData.detail || "Login failed");
			}

			const data = await response.json();
			
			//console.log("Login success:", data);
			//console.log("Login success");
			login(data.access_token, data.email); // Pass the token/user data to your auth context

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

						<div className="login__recaptcha-container">
                            <ReCAPTCHA
                                sitekey={process.env.REACT_APP_RECAPTCHA_SITE_KEY}
                                ref={recaptchaRef}
                            />
                        </div>

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
					<p className="login__signin-paragraph relative z-0">If you do not have an account - <span className="sign__text relative z-0">Create an account!</span></p>
				</Link>
			</div>
		</div>
	);
}