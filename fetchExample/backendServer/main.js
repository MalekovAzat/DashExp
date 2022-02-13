const express = require("express");
const app = express();
const port = 3000;
const path = require("path");

app.get("/get-graph-data", (req, res) => {
  const options = {
    root: path.join(__dirname),
  };
  const fileName = "./array.npy";
  res.sendFile(fileName, options, function (err) {
    if (err) {
      next(err);
    } else {
      console.log("Sent:", fileName);
    }
  });
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
