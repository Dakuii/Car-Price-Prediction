$(document).ready(function(){
    $('#Marque').change(function(){
        var selectedMarque = $(this).val();
        $.ajax({
            type: 'POST',
            url: '/get_models',
            data: { 'Marque': selectedMarque },
            success: function(response){
                $('#Modele').empty();
                $.each(response.models, function(index, value){
                    $('#Modele').append('<option value="' + value + '">' + value + '</option>');
                });
            }
        });
    });

    // Soumission du formulaire
    $('form').submit(function(event){
        event.preventDefault(); // Empêcher le formulaire de se soumettre normalement

        // Effectuer une requête AJAX au point de terminaison '/predict'
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: $('form').serialize(), // Sérialiser les données du formulaire
            success: function(response){
                // Mettre à jour le contenu de la div avec le résultat de la prédiction
                $('#prediction-result').html(response);
            }
        });
    });
});