export type Book = { title: string; author: string; note: string };

/* Newest first. One honest line each — if there is nothing specific to say
   about a book, leave it off rather than padding the list. */
export const books: Book[] = [
  {
    title: 'Designing Data-Intensive Applications',
    author: 'Martin Kleppmann',
    note:
      'The chapters on replication and on maintaining derived data are the reason I now write the migration plan before the feature. Running a legacy and a new system side by side and needing both to agree is exactly the problem this book takes seriously.',
  },
  {
    title: 'The Mom Test',
    author: 'Rob Fitzpatrick',
    note:
      'Short, and the most useful non-technical book I have read. As a founding engineer I spent real time building things people had said they wanted. This is about the gap between what users say and what they do.',
  },
  {
    title: 'Clean Code',
    author: 'Robert C. Martin',
    note:
      'Helped me two years in and started working against me after that. Naming and small functions are real advice, but taken literally it produces a sprawl of tiny functions you have to reassemble in your head to understand anything. I would hand someone the first few chapters and stop there.',
  },
  {
    title: 'System Design Interview, volumes 1 and 2',
    author: 'Alex Xu',
    note:
      'A good vocabulary for discussing architecture in an hour, and honest about being interview preparation. Nothing in it prepares you for the part where the elegant design meets a fifteen-minute execution ceiling.',
  },
  {
    title: 'Data Structures and Algorithms Made Easy',
    author: 'Narasimha Karumanchi',
    note:
      'Did its job for interviews. I have not opened it since, and none of the problems I have actually hit at work were shaped like the ones in it.',
  },
];
