FullCalendar.globalLocales.push(function () {
  'use strict';

  var ro = {
    code: 'ro',
    week: {
      dow: 1, // Luni este prima zi a săptămânii.
      doy: 4, // Săptămâna care conține 4 ianuarie este prima săptămână a anului.
    },
    buttonText: {
      prev: 'Înapoi',
      next: 'Următor',
      today: 'Astăzi',
      month: 'Lună',
      week: 'Săptămână',
      day: 'Zi',
      list: 'Agendă',
    },
    buttonHints: {
      prev: '$0 înainte',
      next: '$0 următor',
      today(buttonText) {
        return (buttonText === 'Zi') ? 'Astăzi' :
          ((buttonText === 'Săptămână') ? 'Aceasta' : 'Aceasta') + ' ' + buttonText.toLocaleLowerCase()
      },
    },
    viewHint(buttonText) {
      return 'Vizualizare ' + (buttonText === 'Săptămână' ? 'a' : 'a') + ' ' + buttonText.toLocaleLowerCase()
    },
    weekText: 'Săp',
    weekTextLong: 'Săptămână',
    allDayText: 'Toată ziua',
    moreLinkText: 'mai multe',
    moreLinkHint(eventCnt) {
      return `Afișați ${eventCnt} evenimente suplimentare`
    },
    noEventsText: 'Nu sunt evenimente de afișat',
    navLinkHint: 'Mergi la $0',
    closeHint: 'Închide',
    timeHint: 'Ora',
    eventHint: 'Eveniment',
  };

  return ro;

}());
