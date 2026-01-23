import React, { useState, useEffect } from 'react'
import WarningIcon from "../components/WarningIcon";
import CautionIcon from "../components/CautionIcon";
import CloseIcon from "../components/CloseIcon";
import SuccessIcon from "../components/SuccessIcon";

import "../styles/components/toast.css"

const Toast = (
    {
        type = "error",
        icon_size = "medium",
        message,
        duration = 10000,
    }
) => {

    const [visible, setVisible] = useState(true);
    const [closing, setClosing] = useState(false);

    // Handle auto-dismiss
    useEffect(() => {
        const timer = setTimeout(() => handleClose(), duration);
        return () => clearTimeout(timer);
    }, [duration]);

    const handleClose = () => {
        setClosing(true); // Start fade-out
        // Remove from DOM after animation
        setTimeout(() => setVisible(false), 300); // match CSS transition duration
    };

    const icon_size_type = 
        icon_size === "small"
        ? "small"
        : icon_size === "medium"
        ? "medium"
        : icon_size === "large"
        ? "large"
        : ""

    return (
        <div className={`toast toast--${type}  ${closing ? 'toast--closing' : ''}`}>
            <div 
                className="toast__x"
                onClick={handleClose}
            >
                <CloseIcon size="small" />
            </div>

            <div className="toast__content-wrapper">
                <div className="toast__header">
                    {
                        type === "error"
                        ? <WarningIcon size={icon_size_type} />
                        : type === "caution"
                        ? <CautionIcon size={icon_size_type} />
                        : type === "success"
                        ? <SuccessIcon size={icon_size_type} />
                        : <></>
                    }
                    {
                        type === "error"
                        ? <span className="toast__header__text">Error</span>
                        : type === "caution" 
                        ? <span className="toast__header__text">Warning</span>
                        : type === "success" 
                        ? <span className="toast__header__text">Success</span>
                        : <></>
                    }
                </div>

            <span className="toast__message">{message}</span>
            </div>

            <div className={`toast__footer-line toast__footer-line--${type}`}></div>
        </div>
    )
}

export default Toast
