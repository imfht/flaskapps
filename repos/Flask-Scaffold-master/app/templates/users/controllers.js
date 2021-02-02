angular.module('myApp.services').factory('User', function($resource) {
  return $resource('api/v1/users/:id.json', { id:'@users.id' }, {
    update: {
      method: 'PATCH',
      
     
     
    }
    }, {
    stripTrailingSlashes: false
    });
});


angular.module('myApp.controllers').controller('UserListController', function($scope, $state,  User, $auth, toaster, 
                                                                                     DTOptionsBuilder) {
        
        
        $scope.dtOptions = DTOptionsBuilder.newOptions()
                            .withBootstrap();
          
        User.get(function(data) {
                     $scope.users = [];
                     angular.forEach(data.data, function(value, key)
                                                        {
                                                       this.user = value.attributes;
                                                       this.user['id'] = value.id;
                                                       this.push(this.user);                    
                                                        },   $scope.users); 
                  
                               }, 
                function(error){
                      $scope.error = error.data;
                                              });
  
  
   $scope.deleteUser = function(selected_id) { // Delete a User. Issues a DELETE to /api/users/:id
      user = User.get({ id: selected_id});
      user.$delete({ id: selected_id},function() {
        toaster.pop({
                type: 'success',
                title: 'Sucess',
                body: "User deleted successfully",
                showCloseButton: true,
                timeout: 0
                });
      
        $state.reload();
      }, function(error) {
         toaster.pop({
                type: 'error',
                title: 'Error',
                body: error,
                showCloseButton: true,
                timeout: 0
                });;
    });
    };
  
}).controller('UserEditController', function($scope, $state, $stateParams, toaster, $window, User, Role) {
     $scope.loading = false;
     
     Role.get(function(data) {
                     $scope.roles = [];
                     angular.forEach(data.data, function(value, key)
                                                        {
                                                       this.role = value.attributes;
                                                       this.role['id'] = value.id;
                                                       this.push(this.role);
                                                     },   $scope.roles);



                                     },
                function(error){
                  toaster.pop({
                         type: 'error',
                         title: 'Error',
                         body: error,
                         showCloseButton: true,
                         timeout: 0
                         });
                                              });
     $scope.updateUser = function() { //Update the user. Issues a PATCH to /v1/api/users/:id
     
     $scope.loading = true;
    $scope.user.$update({ id: $stateParams.id },function() {
     toaster.pop({
                type: 'success',
                title: 'Sucess',
                body: "Update was a success",
                showCloseButton: true,
                timeout: 0
                });
        
       $state.go('users.list');
       $scope.loading = false;
      //$state.go('sites'); // on success go back to home i.e. sites state.
    }, function(error) {
    toaster.pop({
                type: 'error',
                title: 'Error',
                body: error,
                showCloseButton: true,
                timeout: 0
                });
      $scope.loading = false;
    });
  };

  
  $scope.loadUser = function() { //Issues a GET request to /api/users/:id to get a user to update
                       $scope.user = User.get({ id: $stateParams.id },
                                       function() {}, function(error) {
                                          toaster.pop({
                                                type: 'error',
                                                title: 'Error',
                                                body: error,
                                                showCloseButton: true,
                                                timeout: 0
                                                });
                                                });
                                };

  $scope.loadUser(); // Load a user 
  }).controller('UserCreateController', function($scope, $state, User, toaster, Role) {
          $scope.user = new User(); 
          $scope.loading = false;
          
          Role.get(function(data) {
                     $scope.roles = [];
                     angular.forEach(data.data, function(value, key)
                                                        {
                                                       this.role = value.attributes;
                                                       this.role['id'] = value.id;
                                                       this.push(this.role);
                                                     },   $scope.roles);



                                     },
                function(error){
                  toaster.pop({
                         type: 'error',
                         title: 'Error',
                         body: error,
                         showCloseButton: true,
                         timeout: 0
                         });
                                              });

         $scope.addUser = function() { //Issues a POST to v1/api/user.json
                                $scope.loading = true;
                                $scope.user.data.type = "users";
                                $scope.user.$save(function() {
                                toaster.pop({
                                            type: 'success',
                                            title: 'Sucess',
                                            body: "User saved successfully",
                                            showCloseButton: true,
                                            timeout: 0
                                            });
                                   $state.go('users.list');
                                   $scope.loading = false; 
                                }, function(error) {
                                toaster.pop({
                                            type: 'error',
                                            title: 'Error',
                                            body: error,
                                            showCloseButton: true,
                                            timeout: 0
                                            });
                                 $scope.loading = false;
                                           });
                                 };
});




  