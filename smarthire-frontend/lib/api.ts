import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

const API = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export const uploadResume = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  return API.post("/api/ranking/upload-resume", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};
