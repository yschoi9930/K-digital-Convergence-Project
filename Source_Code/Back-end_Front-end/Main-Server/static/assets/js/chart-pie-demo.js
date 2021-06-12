// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Pie Chart Example
var ctx_g = document.getElementById("myPieChart-gender");
ctx_g.style.height = "240px";
var myPieChart_g = new Chart(ctx_g, {
  type: 'doughnut',
  data: {
    labels: ["남자", "여자"],
    datasets: [{
      data: [pie_data.man, pie_data.woman],
      backgroundColor: ['#4e73df', '#1cc88a'],
      hoverBackgroundColor: ['#2e59d9', '#17a673'],
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 10,
      yPadding: 10,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: false
    },
    cutoutPercentage: 80,
  },
});

var ctx_a = document.getElementById("myPieChart-age");
ctx_a.style.height = "240px";
var myPieChart_a = new Chart(ctx_a, {
  type: 'doughnut',
  data: {
    labels: ["kids", "2030", "4050", "silver"],
    datasets: [{
      data: [pie_data.kids, pie_data.age_2030, pie_data.age_4050, pie_data.silver],
      backgroundColor: ['#4e73df', '#1cc88a', '#df73e9', '#b9ee65'],
      hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf', '#943a80'],
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: false
    },
    cutoutPercentage: 80,
  },
});

var ctx_c = document.getElementById("myPieChart-classification");
ctx_c.style.height = "240px";
var myPieChart_c = new Chart(ctx_c, {
  type: 'doughnut',
  data: {
    labels: ["kids", "2030 여자", "2030 남자", "4050 여자", "4050 남자", "silver"],
    datasets: [{
      data: [pie_data.kids, pie_data.age_2030w, 
            pie_data.age_2030m, pie_data.age_4050w, 
            pie_data.age_4050m, pie_data.silver],
      backgroundColor: ['#4e73df', '#5e72e4', '#2dce89', '#df73e9', '#f3677e', '#b9ee65'],
      hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf', '#943a80', '#8d3145', '#6d8f1f'],
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: false
    },
    cutoutPercentage: 80,
  },
});
