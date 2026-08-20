export type Shelf = 'formative' | 'reservations' | 'scaffolding';

export type Book = {
  title: string;
  author: string;
  shelf: Shelf;
  note: string;
};

export const shelves: { id: Shelf; label: string; blurb?: string }[] = [
  {
    id: 'formative',
    label: 'Changed how I work',
  },
  {
    id: 'reservations',
    label: 'Useful, with reservations',
  },
  {
    id: 'scaffolding',
    label: 'Interview scaffolding',
    blurb:
      'Listed because leaving them out would be dishonest. They are good at what they are for, which is passing interviews, not building systems.',
  },
];

/* One honest line each. No covers, no star ratings, no list of books
   I intend to read one day. */
export const books: Book[] = [
  {
    title: 'Designing Data-Intensive Applications',
    author: 'Martin Kleppmann',
    shelf: 'formative',
    note:
      'The chapters on replication and on maintaining derived data are the reason I now write the migration plan before the feature. Running a legacy and a new system side by side and needing both to agree is exactly the problem this book takes seriously.',
  },
  {
    title: 'The Mom Test',
    author: 'Rob Fitzpatrick',
    shelf: 'formative',
    note:
      'Short, and the most useful non-technical book I have read. As a founding engineer I spent a lot of time building things people had said they wanted. This is about the difference between what users say and what they do.',
  },
  {
    title: 'Clean Code',
    author: 'Robert C. Martin',
    shelf: 'reservations',
    note:
      'Helped me two years in and started working against me after that. Naming and small functions are real advice, but followed literally it produces a sprawl of tiny functions you have to reassemble in your head to understand anything. I would hand a junior engineer the first few chapters and stop there.',
  },
  {
    title: 'System Design Interview, volumes 1 and 2',
    author: 'Alex Xu',
    shelf: 'scaffolding',
    note:
      'A good vocabulary for talking about architecture in an hour. Not a substitute for having operated any of it: nothing in here prepares you for the part where the elegant design meets a fifteen-minute execution ceiling.',
  },
  {
    title: 'Data Structures and Algorithms Made Easy',
    author: 'Narasimha Karumanchi',
    shelf: 'scaffolding',
    note:
      'Did its job. I have not opened it since, and none of the interesting problems I have hit at work were shaped like the ones in it.',
  },
];
