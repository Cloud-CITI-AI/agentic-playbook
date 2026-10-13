// Worked example: k6 load smoke test run against staging after deploy; thresholds mirror the SLO.
import http from "k6/http";
import { check } from "k6";

export const options = {
  vus: 20,
  duration: "2m",
  thresholds: {
    http_req_failed: ["rate<0.001"],        // 99.9% success SLO
    http_req_duration: ["p(95)<300", "p(99)<800"],
  },
};

export default function () {
  const res = http.get(`${__ENV.BASE_URL}/v1/orders?status=open&limit=20`, { headers: { Authorization: `Bearer ${__ENV.TEST_TOKEN}` } });
  check(res, { "status is 200": (r) => r.status === 200 });
}
