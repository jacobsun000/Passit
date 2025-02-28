import { useEffect, useState } from "react";
import axios from "axios";

function App() {
  const [data, setData] = useState(null);
  const [keyLogs, setKeyLogs] = useState([]);

  useEffect(() => {
    // Fetch API data
    axios.get("http://192.168.1.98/answer") // Adjust URL if hosted remotely
      .then(response => setData(response.data))
      .catch(error => console.error("Error fetching data:", error));

    // Keyboard event listener
    const handleKeyDown = (event) => {
      setKeyLogs(prevLogs => [...prevLogs, event.key]); // Append key press to logs
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h1>LLM Response</h1>
      {data ? (
        <>
          <div style={{ border: "1px solid #ccc", padding: "10px" }}>
            <div dangerouslySetInnerHTML={{ __html: data.content }} />
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

      <br />
      <h2>Keyboard Activity</h2>
      <div style={{ border: "1px solid #ccc", padding: "10px", minHeight: "50px" }}>
        {keyLogs.length > 0 ? keyLogs.join(" ") : "Press any key..."}
      </div>
    </div>
  );
}

export default App;
