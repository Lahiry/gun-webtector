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
        const response_video = await fetch("http://localhost:5000/process_video", {
          method: "POST",
          body: formData,
        });

        const fileBlob_video = await response_video.blob();
        const url_video = URL.createObjectURL(fileBlob_video);

        const a_video = document.createElement("a");
        document.body.appendChild(a_video);
        a_video.style = "display: none";
        a_video.href = url_video;
        a_video.download = "processed_video.webm";
        a_video.click();
        window.URL.revokeObjectURL(url_video);

        const response_img = await fetch("http://localhost:5000/get_graph", {
          method: "GET"
        });

        const fileBlob_img = await response_img.blob();
        const url_img = URL.createObjectURL(fileBlob_img);

        const a_img = document.createElement("a");
        document.body.appendChild(a_img);
        a_img.style = "display: none";
        a_img.href = url_img;
        a_img.download = "detections_graph.png";
        a_img.click();
        window.URL.revokeObjectURL(url_img);

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
