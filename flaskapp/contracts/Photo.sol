pragma solidity ^0.4.23;

contract Photo {

    struct User{
        uint user_Number;
        address user_Address;
        //bytes32 name;
       // bytes32 emailAddress;
        uint[] registeredPhoto;  // 자기가 업로드한 사진 번호
        bool isUser;
    }

    struct Image{   // :만
        uint256 image_Number; // 사진 번호
        //string imageHash;  // 사진의 해쉬값
        address author; // 사진주인의 userAddress
        //uint256 value;  // 사진의 가격
        uint256 like_count; // 좋아요 수
        bool isPhoto;
    }


    mapping (uint => User) public users_num;
    mapping (address => User) public users_addr;
    address public owner;
    //uint public user_num; // 전역변수 유저 배열 접근하는 인덱스 : 만
    mapping (uint => Image) public images_by_number;   // 사진 번호로 사진에 접근 : 만
    mapping (address => Image) public images_by_addr;   // 사진 번호로 사진에 접근 : 만
    uint256 public userNumber;
    uint256 public imageNumber;

    event LogSignUp(
        uint _usernumber,
        address _useraddress,
       // bytes32 _name,
        //bytes32 _emailaddress
        uint[] _registeredphoto
    );

    event LogRegistImage(   // : 만
        uint256 _imageNumber,
        //string _imageHash,
        address _author,
        //uint256 _value,
        uint256 _like_count
    );

    event LogLikePhoto(
        uint256 _imageNumber,
        uint256 _like_count
    );

    constructor() public{
        owner = msg.sender;
    }
    function signUp() public payable {
        userNumber = userNumber + 1;

        users_num[userNumber] = User(
            userNumber,
            msg.sender,
            //_name,
          //  _emailAddress,
            new uint[](0),
            true
        );

        users_addr[msg.sender] = User(
            userNumber,
            msg.sender,
            //_name,
            //_emailAddress,
            new uint[](0),
            true
        );
        owner.transfer(msg.value);
        
        emit LogSignUp(
            userNumber,
            msg.sender,
            //users_addr[msg.sender].name,
            //users_addr[msg.sender].emailAddress
            users_addr[msg.sender].registeredPhoto
        );

    }

    function registImage() public payable {   // : 만 (사진 업로드)

        imageNumber = imageNumber + 1;

        images_by_number[imageNumber] = Image(
            imageNumber,
            //_image_hash_number,
            msg.sender,
            //_image_value,
            0,
            true
        );
        images_by_addr[msg.sender] = Image(
            imageNumber,
            //_image_hash_number,
            msg.sender,
            //_image_value,
            0,
            true
        );

        //users_addr[msg.sender].registeredPhoto.push(imageNumber);
        owner.transfer(msg.value);
        emit LogRegistImage(
            imageNumber,
            //_image_hash_number,
            msg.sender,
            //_image_value,
            0
        );

    }
    /*
    function likePhoto(uint _imageNumber) public returns (bool){    // 좋아요 누르기
        images_by_number[_imageNumber].like_count++;

        emit LogLikePhoto(
            _imageNumber,
            images_by_number[_imageNumber].like_count
        );

        return true;
    }
    */
    function getIsUserValid() public view returns (bool) {
        return users_addr[msg.sender].isUser;
    }

    function getIsPhotoValid() public view returns (bool) {
        return images_by_addr[msg.sender].isPhoto;
    }

    /*
    function getPhotoState(uint _imageNumber) public view returns (string, address, uint) {
        Image memory image = images_by_number[_imageNumber];
        return (image.imageHash, image.author, image.like_count);
    }*/
/*
    function getUserRigesteredPhoto() public view returns (uint, address, uint[]){
        User memory user = users_addr[msg.sender];
        return (user.user_Number, user.user_Address, user.registeredPhoto);
    }
 */   
    /*function getUserInfo(uint _id) public view returns(bytes32, bytes32){
        User memory user = users_num[_id];
        return (user.name, user.emailAddress);
    }*/
}