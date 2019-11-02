$(document).ready(function () {
    var web3Provider;
    var contracts = {};

    if(typeof web3 !== "undefined"){
        web3Provider = web3.currentProvider;
    }else {
        web3Provider = new web3Provider.providers.HttpProvider("http://localhost:7545");
    }
    web3 = new Web3(web3Provider);

    function enroll(){
        var hashValue=document.getElementById("hashValue").innerText;
    }

    $.getJSON("Photo.json", function(data){
   
        var Artifact = data;
        console.log(Artifact);
        
        contracts.Photo = TruffleContract(Artifact);
        contracts.Photo.setProvider(web3Provider);
        contracts.Photo.deployed().then(async function(instance){
            var newUser = getUserAccount();
            console.log(newUser);
            await instance.registImage({from: newUser}).then(function(tx){
          console.log(tx.receipt);
          
            });
        });
    });
    
    setInterval(function() {
        $.getJSON("Photo.json", function(data){
            var Artifact = data;
            contracts.Photo = TruffleContract(Artifact);
            contracts.Photo.setProvider(web3Provider);
            
            contracts.Photo.deployed().then(function(instance){
                var newmember = getUserAccount();
                instance.getIsPhotoValid({from: newmember}).then(function(res){
                    // console.log(res);
                    if(res == true){
                        location.href ="/mainEnroll";
                    }
                });
            });
        });
    }, 3000);
});

function getUserAccount(){
    var account;
    web3.eth.getAccounts(function(err, accounts){
        account = accounts[0];
    });
    return account;
}