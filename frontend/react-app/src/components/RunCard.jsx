import React, { useState } from 'react'
import ToggleSwitch from "./ToggleSwitch"

import "../styles/components/run_card.css"

const RunCard = (
    {
        run_name_id,
        username,
        attack_type,
        date,
        status,
        attack_model,
        target_model,
        isPublicValue = false,
        canChangeStatus = true,
    }
) => {
    const [isPublic, setIsPublic] = useState(isPublicValue);
    const handleIsPublic = (newValue) => {
        if(canChangeStatus) setIsPublic(newValue);
    }

    const status_class = status === "Ongoing"
    ? "run-card__header-info__status--ongoing"
    : status === "Loading" 
    ? "run-card__header-info__status--loading"
    : status === "Finished"
    ? "run-card__header-info__status--finished" 
    : ""

    return (
        <div className="run-card__container">
            <div className="run-card__content__wrapper">
                <div className="run-card__header">
                    <div className="run-card__header-top">
                        <p className="run-card__header__title">{run_name_id}</p>

                        <ToggleSwitch 
                            checked={isPublic}
                            onChange={handleIsPublic}
                        />
                    </div>
                    <div className="run-card__header-info">

                        <p className="run-card__header-info__text">
                            {username}
                        </p>
                        <span className="run-card__header-info__divisor"></span>
                        <p className="run-card__header-info__text">
                            {attack_type}
                        </p>
                        <span className="run-card__header-info__divisor"></span>
                        <p className="run-card__header-info__text">
                            {date}
                        </p>
                        <span className="run-card__header-info__divisor"></span>
                        <p className={`run-card__header-info__text ${status_class}`}>
                            {status === "Loading" ? `${status}...` : status}
                        </p>
                    </div>
                </div>

                <div className="run-card__footer">
                    <div className="run-card__footer__attack">
                        <p className="run-card__footer__attack__title">
                            Attack Model
                        </p>
                        <p className="run-card__footer__attack__model-name">
                            {attack_model}
                        </p>
                    </div>

                    <p className="run-card__footer__versus">VS</p>
                    
                    <div className="run-card__footer__target">
                        <p className="run-card__footer__target__title">
                            Target Model
                        </p>
                        <p className="run-card__footer__target__model-name">
                            {target_model}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default RunCard;