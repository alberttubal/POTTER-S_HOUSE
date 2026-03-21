export type BuffetPackageSet = {
  name: string;
  items: string[];
};

export type BuffetPackage = {
  id: string;
  title: string;
  price: number;
  minPax: number;
  note?: string;
  summary: string;
  images: string[];
  sets: BuffetPackageSet[];
};

export const buffetPackages: BuffetPackage[] = [
  {
    id: "standard-buffet",
    title: "Standard Buffet",
    price: 295,
    minPax: 50,
    summary: "Perfect for casual gatherings with balanced favorites.",
    images: [
      "https://images.unsplash.com/photo-1661994215679-cde7c2c5c060?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxidWZmZXQlMjB0YWJsZSUyMGZpbGlwaW5vfGVufDF8fHx8MTc3MzAzNDQyOHww&ixlib=rb-4.1.0&q=80&w=1200",
      "https://images.unsplash.com/photo-1658925111653-2c08083c08ff?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwb3JrJTIwZGlzaCUyMGZvb2R8ZW58MXx8fHwxNzczMDM0NDMxfDA&ixlib=rb-4.1.0&q=80&w=1200",
      "https://images.unsplash.com/photo-1609834265242-75d58b7db409?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxzZWFmb29kJTIwZmVhc3R8ZW58MXx8fHwxNzczMDM0NDMyfDA&ixlib=rb-4.1.0&q=80&w=1200"
    ],
    sets: [
      {
        name: "Set A",
        items: [
          "Sotanghon",
          "Beef Steak",
          "Chili Wings",
          "Four Seasons",
          "Sweet 'n' Sour Fish",
          "Mango Tapioca",
          "Rice",
          "Softdrinks"
        ]
      },
      {
        name: "Set B",
        items: [
          "Bam-I",
          "Beef w/ Mushroom",
          "Battered Chicken",
          "Four Seasons",
          "Kinilaw",
          "Macaroni Salad",
          "Rice",
          "Softdrinks"
        ]
      },
      {
        name: "Set C",
        items: [
          "Pancit Guisado",
          "Beef w/ Mushroom",
          "Honey Buttered Chicken",
          "Fish Fillet w/ Sauce",
          "Lumpia Shanghai",
          "Fresh Fruit Salad",
          "Rice",
          "Softdrinks"
        ]
      }
    ]
  },
  {
    id: "premium-buffet",
    title: "Premium Buffet",
    price: 345,
    minPax: 50,
    summary: "Elevated menu with premium dish choices.",
    images: [
      "https://images.unsplash.com/photo-1767324672816-e09a2a0a3979?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmcmllZCUyMGNoaWNrZW4lMjBidWZmZXR8ZW58MXx8fHwxNzczMDM0NDMxfDA&ixlib=rb-4.1.0&q=80&w=1200",
      "https://images.unsplash.com/photo-1679279726940-be5ce80c632c?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwYW5jaXQlMjBub29kbGVzfGVufDF8fHx8MTc3MzAzNDQzMXww&ixlib=rb-4.1.0&q=80&w=1200"
    ],
    sets: [
      {
        name: "Set A",
        items: [
          "Battered Chicken",
          "Beef Steak",
          "Breaded Fish w/ Tartar Sauce",
          "Lasagna",
          "Sotanghon",
          "Four Seasons",
          "Revel Bars",
          "Rice",
          "Softdrinks"
        ]
      },
      {
        name: "Set B",
        items: [
          "Pancit Guisado",
          "Beef Stew",
          "Fish Fillet w/ Sauce",
          "Chicken 'n' Mushroom",
          "Four Seasons",
          "Mango Tapioca",
          "Rice",
          "Softdrinks"
        ]
      }
    ]
  },
  {
    id: "deluxe-buffet",
    title: "Deluxe Buffet",
    price: 385,
    minPax: 50,
    note: "Includes 6 sets table/chairs and food handlers",
    summary: "Premium feast with top selections and setups.",
    images: [
      "https://images.unsplash.com/photo-1654579920979-8ebb4e96b755?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxiZWVmJTIwc3RlYWslMjBmaWxpcGlub3xlbnwxfHx8fDE3NzMwMzQ0Mjh8MA&ixlib=rb-4.1.0&q=80&w=1200",
      "https://images.unsplash.com/photo-1713763937171-7f729b7681bf?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxkZXNzZXJ0JTIwcGFzdHJpZXN8ZW58MXx8fHwxNzczMDM0NDMxfDA&ixlib=rb-4.1.0&q=80&w=1200"
    ],
    sets: [
      {
        name: "Set A",
        items: [
          "Potato Salad",
          "Beef w/ Brocolli",
          "Sweet 'n' Sour Fish",
          "Chicken Cordon Bleu",
          "Lasagna",
          "Lumpia Shanghai",
          "Brownies",
          "Rice",
          "Softdrinks"
        ]
      },
      {
        name: "Set B",
        items: [
          "Four Seasons",
          "Beef w/ Mushroom",
          "Grilled Chicken",
          "Seafoods mix in Cajun Sauce",
          "Sweet 'n' Sour Fish",
          "Lasagna",
          "Fruit Salad",
          "Rice"
        ]
      }
    ]
  }
];

export function getBuffetPackage(id: string) {
  return buffetPackages.find((pkg) => pkg.id === id) ?? null;
}
