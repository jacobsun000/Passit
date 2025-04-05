import { useEffect, useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

function App() {
  const [data, setData] = useState(null);

  const fetchData = () => {
    axios.get("http://192.168.1.235:8081/answer") // Adjust URL if hosted remotely
      .then(response => setData(response.data))
      .catch(error => console.error("Error fetching data:", error));
  };

  useEffect(() => {
    // Initial API fetch
    fetchData();

    // Full-screen tap event listener
    const handleFullScreenTap = () => {
      console.log("Full-screen tap detected!");
      fetchData(); // Trigger API request on tap
    };

    window.addEventListener("touchstart", handleFullScreenTap);

    return () => {
      window.removeEventListener("touchstart", handleFullScreenTap);
    };
  }, []);

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h3>LLM Response</h3>
      {data ? (
        <>
          <div style={{ border: "1px solid #ccc", padding: "10px", textAlign: "left" }}>
            <ReactMarkdown>{data.content}</ReactMarkdown>  {/* Render markdown properly */}
          </div>
          <br />
          <h2>Captured Image:</h2>
          <div style={{ border: "1px solid #ccc", padding: "10px" }}>
            <img src={`data:image/png;base64,${data.image}`} width="400" alt="Captured" />
          </div>
        </>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
}

export default App;
