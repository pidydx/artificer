var artificerApp = angular.module('artificer', []);

artificerApp.controller('artificerCtrl', function($scope, $http) {
    get_artifacts_index();
    function get_artifacts_index(){
        $http.get("http://localhost:6543/api/artifacts")
      .then(function(response){ $scope.artifacts = response.data.artifacts; });
    }
});