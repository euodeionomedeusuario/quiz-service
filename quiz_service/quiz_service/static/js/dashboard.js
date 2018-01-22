/*dashboard.js*/

/**/

$(document).ready(function(){
  /*Habilitando o uso de efeitos do Materialize nos selects*/
  $('select').material_select();

  // Initialize collapse button
  $(".button-collapse").sideNav();
  // Initialize collapsible (uncomment the line below if you use the dropdown variation)
  $('.collapsible').collapsible();

  function createTest(test) {
    $test = $("<tr />")
              .append($("<td />")
                .attr("name", "name")
                .text(test["name"]))
              .append($("<td />")
                .attr("name", "description")
                .text(test["description"]))
              .append($("<td />")
                .attr("name", "option")
                  .append($("<a />"))
                    .attr("href", "#")
                    .text("Compartilhar"))

    return $test;
  }

  function loadTests() {
      $.ajax({
        url: "http://127.0.0.1/quiz_service/tests/",
        type: "GET",
        success: function(data) {
          for(index in data) {
            $("#tests").append(createTest(data[index]));
          }
        }
      });
  }

  /*Criando um novo tópico*/
  function createTopic(topic) {
    $topic = $("<option />").text(topic["name"]).attr("value", topic["_id"]);

    return $topic;

  }

  /*Criando uma nova disciplina*/
  function createCourse(course) {
    $course = $("<option />").text(course["name"]).attr("value", course["_id"]);

    return $course;

  }

  /*Criando uma nova questão*/
  function createQuestion(question) {
    $question = $("<li />")
                .addClass("row")
                  .append($("<input />")
                    .attr("type", "hidden")
                    .attr("value", question["_id"]))
                  .append($("<p />")
                    .text(question["title"]));


     return $question
  }

  /*Carregando disciplinas disponíveis no BD*/
  function loadCourses() {
    $.ajax({
      url: "http://127.0.0.1:5000/quiz_service/courses/",
      type: "GET",
      success: function(data) {
        for(index in data) {
          $("#course").append(createCourse(data[index]));
        }
        /*Recarregando as configurações de efeitos do Materialize nos selects*/
        $('select').material_select();
      }
    });
  }

  loadCourses();

  /*Carregando os tópicos no BD*/
  function loadTopics(course) {
    $.ajax({
      url: "http://127.0.0.1:5000/quiz_service/topics/",
      type: "POST",
      data: {course: course},
      success: function(data) {
        for(index in data) {
          $("#topic").append(createTopic(data[index]));
        }
        /*Recarregando as configurações de efeitos do Materialize nos selects*/
        $('select').material_select();
      }
    });
  }

  /*Carregando tópicos quando disciplina selecionada*/
  $("#course").change(function(event) {
    var course = $("select#course").val();
    loadTopics(course);
  });

  /*Atualizando níveis*/
  $(".level").change(function(event) {
    var $level = [] /*Nível da questão*/

    $(".level").each(function(index, element) {
      $level.push($(this));
    });

    $level[0].attr("max", 100 - $level[1].val() - $level[2].val())
    $level[1].attr("max", 100 - $level[0].val() - $level[2].val())
    $level[2].attr("max", 100 - $level[0].val() - $level[1].val())

  });


  /*Carregando questões consultadas no BD*/
  function loadQuestions(course, topic, number, level, type) {
    $.ajax({
      url: "http://127.0.0.1:5000/quiz_service/test/" + course + "/" + topic + "/",
      type: "POST",
      /*Melhore esta parte*/
      data: {number: number, easy: level[0], medium: level[1], hard: level[2], type: type},
      success: function(data) {
        for(index in data) {
          $("#questions-list").append(createQuestion(data[index]));
        }
      }
    });
  }

  /*Pesquisando uma lista de questões por tópico*/
  $("#btnSearch").click(function(event) {
    $("#questions-list").empty();

    var course = $("select#course").val(); /*ID do curso*/
    var topic = $("select#topic").val(); /*ID do tópico*/
    var number = $("#number").val(); /*Número de questões*/
    var type = $("#type :checked").val(); /*Tipo de questão*/
    var level = [] /*Nível da questão*/

    $(".level").each(function(index, element) {
      level.push($(this).val());
    });

    loadQuestions(course, topic, number, level, type);
  });

  /*Salvando teste*/
  function saveTest(name, description, questions) {
      $.ajax({
        url: "http://127.0.0.1:5000/quiz_service/tests/",
        type: "POST",
        data: {"name": name, "description": description, "questions": questions},
        success: function(data) {
          console.log("New test saved in " + Date());
        }
      });
  }

  /*Adicionando evento para o botão de salvar teste*/
  $("#btnSave").click(function(event) {
    var name = $("#name").val();
    var description = $("#description").val();
    var questions = [];

    $("#questions-list li input").each(function(index, element) {
      questions.push($(this).val());
    });

    saveTest(name, description, questions);
  });

});
