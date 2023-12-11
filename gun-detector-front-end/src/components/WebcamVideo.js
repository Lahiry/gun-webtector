import Webcam from "react-webcam";
import React, { useRef, useState } from "react";

export function WebcamVideo() {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [capturing, setCapturing] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [downloading, setDownloading] = useState(false);

  // Start capturing video
  const handleStartCaptureClick = () => {
    if (!downloading) {
      setCapturing(true);
      setRecordedChunks([]);
      mediaRecorderRef.current = new MediaRecorder(webcamRef.current.stream, {
        mimeType: "video/webm",
      });
      mediaRecorderRef.current.addEventListener(
        "dataavailable",
        handleDataAvailable
      );
      mediaRecorderRef.current.start();
    }
  };

  // Handle data available during recording
  const handleDataAvailable = ({ data }) => {
    if (data.size > 0) {
      setRecordedChunks((prev) => prev.concat(data));
    }
  };

  // Stop capturing video
  const handleStopCaptureClick = () => {
    if (!downloading) {
      mediaRecorderRef.current.stop();
      setCapturing(false);
    }
  };

  // Download recorded video with detections and detection graph image
  const handleDownload = async () => {
    if (recordedChunks.length && !downloading) {
      setDownloading(true);

      const blob = new Blob(recordedChunks, {
        type: "video/webm",
      });

      const formData = new FormData();
      formData.append("video", blob);

      try {
        // Fetch processed video
        const response_video = await fetch("http://localhost:5000/process_video", {
          method: "POST",
          body: formData,
        });

        // Extract and download processed video
        const fileBlob_video = await response_video.blob();
        const url_video = URL.createObjectURL(fileBlob_video);

        const a_video = document.createElement("a");
        document.body.appendChild(a_video);
        a_video.style = "display: none";
        a_video.href = url_video;
        a_video.download = "processed_video.webm";
        a_video.click();
        window.URL.revokeObjectURL(url_video);

        // Fetch detections graph image
        const response_img = await fetch("http://localhost:5000/get_graph", {
          method: "GET"
        });

        // Extract and download detections graph image
        const fileBlob_img = await response_img.blob();
        const url_img = URL.createObjectURL(fileBlob_img);

        const a_img = document.createElement("a");
        document.body.appendChild(a_img);
        a_img.style = "display: none";
        a_img.href = url_img;
        a_img.download = "detections_graph.png";
        a_img.click();
        window.URL.revokeObjectURL(url_img);

        // Reset recorded chunks
        setRecordedChunks([]);
      } finally {
        // Reset downloading state
        setDownloading(false);
      }
    }
  };

  return (
    <>
      <Webcam audio={false} ref={webcamRef} />
      {capturing ? (
        <button onClick={handleStopCaptureClick} className="stop_recording">
          Stop Capture
        </button>
      ) : (
        <button
          onClick={handleStartCaptureClick}
          className={!downloading ? "start_recording" : "start_recording_disabled"}
        >
          Start Capture
        </button>
      )}
      {recordedChunks.length > 0 && !capturing && (
        <button onClick={handleDownload} disabled={downloading} className={downloading ? "downloading" : "download"}>
          {downloading ? "Downloading..." : "Download"}
        </button>
      )}
    </>
  );
}
