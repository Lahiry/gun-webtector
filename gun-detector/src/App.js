import "./App.css";
import { Header } from "./components/Header";
import { WebcamVideo } from "./components/WebcamVideo";

function App() {
  return (
    <>
      <Header />
      <div className="App">
        <WebcamVideo/>
      </div>
    </>
  );
}

export default App;