import { Card } from "@mui/material";
import axios from "axios";
import { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import { useFilter } from "./FilterProvider";

const optionsBar = {
  responsive: true,
  indexAxis: "y",
  maintainAspectRatio: false,

  // barThickness: 6,
  plugins: {
    legend: {
      // position: 'top',
      // display: true,
    },
    title: {
      display: true,
      text: "Total number of tweets for individual topics",
    },
  },
};
const BarChart = () => {
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(false);
  let { startDate, endDate } = useFilter();

  useEffect(() => {
    let params = new URLSearchParams([["all", true]]);
    params.append("start_date", startDate);
    params.append("end_date", endDate);
    // if (year !== "none" && month !== "none") {
    //   params.append("month", `${year}-${month}`);
    // }
    axios
      .get(`/pseudo_tweets/count`, { params })
      .then((data) => data.data)
      .then((data) => {
        let dataTemp = [];
        for (let key in data) {
          if (key !== "total") {
            dataTemp.push({ label: key, count: data[key] });
          }
        }

        dataTemp.sort((a, b) => b.count - a.count);
        console.log("Bar", dataTemp);

        setData({
          labels: dataTemp.map((datum) => datum.label),
          datasets: [
            {
              label: "Total tweet Count in the given range",
              data: dataTemp.map((datum) => datum.count),
              backgroundColor: "#247881",
            },
          ],
        });
        setLoading(true);
      });
  }, [startDate, endDate]);
  return (
    <>
      {loading && (
        <Card className="w-1/3 ml-3">
          <Bar options={optionsBar} data={data} />
        </Card>
      )}
    </>
  );
};

export default BarChart;
