export function sortByTimestampAsc(items = []) {
  return [...items].sort((leftItem, rightItem) => {
    const leftTimestamp = new Date(leftItem?.timestamp || 0).getTime();
    const rightTimestamp = new Date(rightItem?.timestamp || 0).getTime();

    return leftTimestamp - rightTimestamp;
  });
}

export function sortByTimestampDesc(items = []) {
  return sortByTimestampAsc(items).reverse();
}
