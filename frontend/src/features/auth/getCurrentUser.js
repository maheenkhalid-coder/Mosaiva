import api from "../../lib/axios";

async function getCurrentUser() {
  const { data } = await api.get("/api/me");
  return data;
}

export default getCurrentUser;