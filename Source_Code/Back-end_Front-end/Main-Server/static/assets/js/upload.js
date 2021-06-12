function handleOnChange(e) {
  // 선택된 데이터 가져오기
  const value = e.value;
  
  if (value == 'kids') {
    $('#gender').empty()
    var selected = $("<option selected>타겟 성별을 선택하세요.</option>");
    var option = $("<option value='all'>"+'모두'+"</option>");
    $('#gender').append(selected, option);

  } else if(value == 'silver') {
    $('#gender').empty()
    var selected = $("<option selected>타겟 성별을 선택하세요.</option>");
    var option = $("<option value='all'>"+'모두'+"</option>");
    $('#gender').append(selected, option);

  } else {
    $('#gender').empty()
    var selected = $("<option selected>타겟 성별을 선택하세요.</option>");
    var option = $("<option value='man'>남자</option>");
    var option1 = $("<option value='woman'>여자</option>");
    $('#gender').append(selected, option, option1);

  } 
}

function handleOnChange1(e) {
    // 선택된 데이터 가져오기
    const value = e.value;
    
    if (value == '1') {
      document.getElementById('budget').innerText
        = '200 만원';
    } else if(value == '2') {
      document.getElementById('budget').innerText
        = '400 만원';
    } else {
      document.getElementById('budget').innerText
        = '600 만원';
    } 
}

function handleOnChange2(e) {
  var pack = document.getElementById('addr1');
  var packages = pack.options[pack.selectedIndex].value;

  // 선택된 데이터 가져오기
  const value = e.value;
  if (packages == '서울시') {
    if (value == '1') {
      document.getElementById('budget').innerText
        = '1 억';
    } else if(value == '2') {
      document.getElementById('budget').innerText
        = '2 억';
    } else {
      document.getElementById('budget').innerText
        = '3 억';
    }   
  } else {
    if (value == '1') {
      document.getElementById('budget').innerText
        = '5000 만원';
    } else if(value == '2') {
      document.getElementById('budget').innerText
        = '1 억';
    } else {
      document.getElementById('budget').innerText
        = '1 억 5000 만원';
    }   
  }
  
}

function openZipSearch() {
	new daum.Postcode({
		oncomplete: function(data) {
			$('[name=addr1]').val(data.address);
		}
	}).open();
}

$('#execute').click(function () {
    var gender = $('#gender').val();
    var age = $('#age').val();
    var period = $('#period').val();
    var budget = $('#budget').text();
    var addr1 = $('#addr1').val();

    var postdata = {'target_gender': gender, 'target_age': age, 'period': period, 
                    'budget': budget, 'location': addr1};

    $.ajax({
        type: 'POST',
        url: '/upload',
        data: JSON.stringify(postdata),    
        contentType: "application/json",
        success: function (data) {
            console.log(data);
            window.location = '/s3';
        },
        error: function (request, status, error) {
            alert(error);
        }
    })
})