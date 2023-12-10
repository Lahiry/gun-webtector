import Webcam from "react-webcam";
import React, { useRef, useState, useEffect } from "react";

export function WebcamVideo() {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [capturing, setCapturing] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [downloading, setDownloading] = useState(false);

  const handleStartCaptureClick = () => {
    if (!downloading) {
      setCapturing(true);
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

  const handleDataAvailable = ({ data }) => {
    if (data.size > 0) {
      setRecordedChunks((prev) => prev.concat(data));
    }
  };

  const handleStopCaptureClick = () => {
    if (!downloading) {
      mediaRecorderRef.current.stop();
      setCapturing(false);
    }
  };

  const handleDownload = async () => {
    if (recordedChunks.length && !downloading) {
      setDownloading(true);

      const blob = new Blob(recordedChunks, {
        type: "video/webm",
      });

      const formData = new FormData();
      formData.append("video", blob);

      try {
        const response = await fetch("http://localhost:5000/process_video", {
          method: "POST",
          body: formData,
        });

        const fileBlob = await response.blob();
        const url = URL.createObjectURL(fileBlob);

        const a = document.createElement("a");
        document.body.appendChild(a);
        a.style = "display: none";
        a.href = url;
        a.download = "processed_video.webm";
        a.click();
        window.URL.revokeObjectURL(url);

        setRecordedChunks([]);
      } finally {
        setDownloading(false);
      }
    }
  };

  // Disable start capture button while downloading
  useEffect(() => {
    if (downloading) {
      setCapturing(false);
    }
  }, [downloading]);

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
