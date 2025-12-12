import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="relative px-20 py-28 min-h-[calc(100vh-112px)]">
      <div
        className="absolute right-0 bottom-0 w-1/2 h-4/5 bg-gray-200 -z-5"
        style={{ clipPath: "polygon(0% 100%, 100% 0%, 100% 100%)" }}
      ></div>

      <h1 className="text-7xl font-bold mb-6">
        Automated Red-Teaming<br />of LLMs
      </h1>

      <p className="text-2xl text-gray-700 max-w-3xl mb-10">
        Benchmark LLM security and compare model results all in one platform.
      </p>

      <div className="flex space-x-6">
		<Link to="run_experiment">
			<button className="px-6 py-3 bg-red-600 text-white rounded-md text-lg hover:bg-red-800">
			Run an Experiment
			</button>
		</Link>

		<Link to="/compare">
			<button className="px-6 py-3 bg-white border border-black rounded-md text-lg hover:bg-black hover:text-white">
			Compare LLMs
			</button>
		</Link>
      </div>
    </div>
  );
}
