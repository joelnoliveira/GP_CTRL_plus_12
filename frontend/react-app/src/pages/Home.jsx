import { Link } from "react-router-dom";

import Button from "../components/Button.jsx"
import ArrowUp from "../components/ArrowIcon.jsx"


import "../styles/pages/home.css"
import ArrowIcon from "../components/ArrowIcon.jsx";

export default function Home() {
  return (
    <div className="home">
      <div
        className="home__gray-polygon -z-5"
        style={{ clipPath: "polygon(0% 100%, 100% 0%, 100% 100%)" }}
      ></div>

      <h1 className="home__h1">
        Automated Red-Teaming<br />of LLMs
      </h1>

      <p className="home__paragraph">
        Benchmark LLM security and compare model results all in one platform.
      </p>

      <div className="flex space-x-6">
		<Link to="/run_experiment">
      <Button 
        size={"small"}
        variant={"default"}
        text={"Run an Experiment"}
        styles={"text-lg"}
      />
		</Link>

		<Link to="/compare">
      <Button 
        size={"small"}
        variant={"alternative"}
        text={"Compare LLMs"}
        styles={"text-lg"}
      />
		</Link>
      </div>
    </div>
  );
}
