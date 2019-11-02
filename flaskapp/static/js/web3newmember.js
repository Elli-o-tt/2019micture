var web3Provider;
var contracts = {};

if(typeof web3 !== "undefined"){
    web3Provider = web3.currentProvider;
}else {
    web3Provider = new web3Provider.providers.HttpProvider("http://localhost:7545");
    
}
web3 = new Web3(web3Provider);


function getUserAccounts(){
    var acc ="";
    web3.eth.getAccounts(function(err, accounts){
        acc = accounts[0];
        document.getElementById("AccountList").style.display = "block";
        document.getElementById("MetaAcc").innerText = acc;
    });
}