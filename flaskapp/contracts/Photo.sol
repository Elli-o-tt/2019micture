pragma solidity ^0.4.23;

contract Photo {
    struct User{
        uint userNumber;
        address userAddress;
        string name;
        string emailAddress;
        bytes32[] registeredPhoto;
        bool isUser;
    }

    mapping (uint => User) public users_num;
    mapping (address => User) public users_addr;

    uint public userNumber; // 전역변수 유저 배열 접근하는 인덱스

    event LogSignUp(
        uint _usernumber,
        address _useraddress,
        string _name,
        string _emailaddress,
        bytes32[] _registeredphoto
    );

    function signUp(string _name, string _emailAddress) public returns (bool) {
        userNumber = userNumber + 1;

        users_num[userNumber] = User(
            userNumber,
            msg.sender,
            _name,
            _emailAddress,
            new bytes32[](0),
            true
        );

        users_addr[msg.sender] = User(
            userNumber,
            msg.sender,
            _name,
            _emailAddress,
            new bytes32[](0),
            true
        );

        emit LogSignUp(
            userNumber,
            msg.sender,
            users_addr[msg.sender].name,
            users_addr[msg.sender].emailAddress,
            users_addr[msg.sender].registeredPhoto
        );

        return true;
    }
    function getIsUserValid() public view returns (bool) {
        return users_addr[msg.sender].isUser;
    }
}
