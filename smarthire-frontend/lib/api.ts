import axios from "axios";

const API = axios.create({
  baseURL: "https://smarthire-ai-zm81.onrender.com",
});

export const uploadResume = (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  return API.post("/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};
