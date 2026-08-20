export type Book = { title: string; author: string; note: string; href?: string };

/* Newest first. One honest line each — if there is nothing specific to say
   about a book, leave it off rather than padding the list. Links point at
   Open Library, deliberately not at any affiliate. */
export const books: Book[] = [
  {
    title: 'End-to-End Object Detection with Transformers',
    author: 'Carion et al., 2020',
    href: 'https://arxiv.org/abs/2005.12872',
    note:
      'The paper behind the DETR reimplementation on my work page. Worth reading even if you never build it: it throws out the hand-tuned pipeline of anchors and non-maximum suppression and replaces it with set prediction and a bipartite matching loss.',
  },
  {
    title: 'Designing Data-Intensive Applications',
    author: 'Martin Kleppmann',
    href: 'https://openlibrary.org/works/OL19293745W',
    note:
      'Where I actually learned system design, in depth rather than as a list of terms to drop in an interview.',
  },
  {
    title: 'The Mom Test',
    author: 'Rob Fitzpatrick',
    href: 'https://openlibrary.org/works/OL23982116W',
    note:
      'As the founding engineer at Scream I was in those conversations myself. This is the book that stopped me building things people had merely said yes to.',
  },
  {
    title: 'System Design Interview, volumes 1 and 2',
    author: 'Alex Xu',
    href: 'https://openlibrary.org/works/OL21947791W',
    note:
      'Good on the fundamentals, and the worked examples of designing systems at scale are the part worth the price. Interview preparation, and honest about being that.',
  },
  {
    title: 'Clean Code',
    author: 'Robert C. Martin',
    href: 'https://openlibrary.org/works/OL17618370W',
    note:
      'Read it early on. Its ideas turn up in other people’s code whether or not you agree with them, which is reason enough to have read it.',
  },
  {
    title: 'Data Structures and Algorithms Made Easy',
    author: 'Narasimha Karumanchi',
    href: 'https://openlibrary.org/works/OL24463217W',
    note:
      'It did the job it exists to do, and I have not opened it since.',
  },
];
