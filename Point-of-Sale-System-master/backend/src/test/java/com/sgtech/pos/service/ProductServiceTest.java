package com.sgtech.pos.service;

import com.sgtech.pos.dto.ProductDTO;
import com.sgtech.pos.exception.DuplicateResourceException;
import com.sgtech.pos.exception.ResourceNotFoundException;
import com.sgtech.pos.exception.ValidationException;
import com.sgtech.pos.model.Product;
import com.sgtech.pos.repository.ProductRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.modelmapper.ModelMapper;

import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ProductServiceTest {

    @Mock
    private ProductRepository productRepository;

    @Mock
    private ModelMapper modelMapper;

    @InjectMocks
    private ProductServiceImpl productService;

    private ProductDTO productDTO;
    private Product product;

    @BeforeEach
    void setUp() {
        productDTO = new ProductDTO();
        productDTO.setId(1L);
        productDTO.setName("Test Product");
        productDTO.setCategory("Test Category");
        productDTO.setPrice(10.0);
        productDTO.setQuantity(100);

        product = new Product();
        product.setId(1L);
        product.setName("Test Product");
        product.setCategory("Test Category");
        product.setPrice(10.0);
        product.setQuantity(100);
    }

    @Test
    void createProduct_ValidProduct_ReturnsCreatedProduct() {
        // Arrange
        when(productRepository.existsByName(anyString())).thenReturn(false);
        when(modelMapper.map(productDTO, Product.class)).thenReturn(product);
        when(productRepository.save(any(Product.class))).thenReturn(product);
        when(modelMapper.map(product, ProductDTO.class)).thenReturn(productDTO);

        // Act
        ProductDTO result = productService.createProduct(productDTO);

        // Assert
        assertThat(result).isEqualTo(productDTO);
        verify(productRepository).save(any(Product.class));
    }

    @Test
    void createProduct_InvalidPrice_ThrowsValidationException() {
        // Arrange
        productDTO.setPrice(-1.0);

        // Act & Assert
        assertThatThrownBy(() -> productService.createProduct(productDTO))
            .isInstanceOf(ValidationException.class)
            .hasMessage("Price must be positive");
    }

    @Test
    void createProduct_DuplicateName_ThrowsDuplicateResourceException() {
        // Arrange
        when(productRepository.existsByName(anyString())).thenReturn(true);

        // Act & Assert
        assertThatThrownBy(() -> productService.createProduct(productDTO))
            .isInstanceOf(DuplicateResourceException.class)
            .hasMessage("Product already exists");
    }

    @Test
    void updateProduct_ValidUpdate_ReturnsUpdatedProduct() {
        // Arrange
        ProductDTO updatedDTO = new ProductDTO();
        updatedDTO.setName("Updated Product");
        updatedDTO.setCategory("Updated Category");
        updatedDTO.setPrice(20.0);
        updatedDTO.setQuantity(200);

        Product existingProduct = new Product();
        existingProduct.setId(1L);
        existingProduct.setName("Old Product");

        Product updatedProduct = new Product();
        updatedProduct.setId(1L);
        updatedProduct.setName("Updated Product");
        updatedProduct.setCategory("Updated Category");
        updatedProduct.setPrice(20.0);
        updatedProduct.setQuantity(200);

        when(productRepository.findById(1L)).thenReturn(Optional.of(existingProduct));
        when(productRepository.existsByName(anyString())).thenReturn(false);
        when(productRepository.save(any(Product.class))).thenReturn(updatedProduct);
        when(modelMapper.map(updatedProduct, ProductDTO.class)).thenReturn(updatedDTO);

        // Act
        ProductDTO result = productService.updateProduct(1L, updatedDTO);

        // Assert
        assertThat(result.getName()).isEqualTo("Updated Product");
        assertThat(result.getPrice()).isEqualTo(20.0);
        verify(productRepository).save(existingProduct);
    }

    @Test
    void updateProduct_ProductNotFound_ThrowsResourceNotFoundException() {
        // Arrange
        when(productRepository.findById(1L)).thenReturn(Optional.empty());

        // Act & Assert
        assertThatThrownBy(() -> productService.updateProduct(1L, productDTO))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessage("Product not found");
    }

    @Test
    void getAllProducts_ReturnsAllProducts() {
        // Arrange
        List<Product> products = Arrays.asList(product);
        List<ProductDTO> productDTOs = Arrays.asList(productDTO);

        when(productRepository.findAll()).thenReturn(products);
        when(modelMapper.map(product, ProductDTO.class)).thenReturn(productDTO);

        // Act
        List<ProductDTO> result = productService.getAllProducts();

        // Assert
        assertThat(result).hasSize(1);
        assertThat(result.get(0)).isEqualTo(productDTO);
    }

    @Test
    void getProductById_ProductExists_ReturnsProduct() {
        // Arrange
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));
        when(modelMapper.map(product, ProductDTO.class)).thenReturn(productDTO);

        // Act
        ProductDTO result = productService.getProductById(1L);

        // Assert
        assertThat(result).isEqualTo(productDTO);
    }

    @Test
    void getProductById_ProductNotFound_ThrowsResourceNotFoundException() {
        // Arrange
        when(productRepository.findById(1L)).thenReturn(Optional.empty());

        // Act & Assert
        assertThatThrownBy(() -> productService.getProductById(1L))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessage("Product not found");
    }

    @Test
    void deleteProduct_ProductExists_DeletesProduct() {
        // Arrange
        when(productRepository.existsById(1L)).thenReturn(true);

        // Act
        productService.deleteProduct(1L);

        // Assert
        verify(productRepository).deleteById(1L);
    }

    @Test
    void deleteProduct_ProductNotFound_ThrowsResourceNotFoundException() {
        // Arrange
        when(productRepository.existsById(1L)).thenReturn(false);

        // Act & Assert
        assertThatThrownBy(() -> productService.deleteProduct(1L))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessage("Product not found");
    }

    @Test
    void searchProducts_ReturnsMatchingProducts() {
        // Arrange
        List<Product> products = Arrays.asList(product);
        List<ProductDTO> productDTOs = Arrays.asList(productDTO);

        when(productRepository.findByNameContainingIgnoreCase("test")).thenReturn(products);
        when(modelMapper.map(product, ProductDTO.class)).thenReturn(productDTO);

        // Act
        List<ProductDTO> result = productService.searchProducts("test");

        // Assert
        assertThat(result).hasSize(1);
        assertThat(result.get(0)).isEqualTo(productDTO);
    }

    @Test
    void updateStock_ValidQuantity_ReturnsUpdatedProduct() {
        // Arrange
        Product updatedProduct = new Product();
        updatedProduct.setId(1L);
        updatedProduct.setName("Test Product");
        updatedProduct.setQuantity(150);

        ProductDTO updatedDTO = new ProductDTO();
        updatedDTO.setId(1L);
        updatedDTO.setName("Test Product");
        updatedDTO.setQuantity(150);

        when(productRepository.findById(1L)).thenReturn(Optional.of(product));
        when(productRepository.save(any(Product.class))).thenReturn(updatedProduct);
        when(modelMapper.map(updatedProduct, ProductDTO.class)).thenReturn(updatedDTO);

        // Act
        ProductDTO result = productService.updateStock(1L, 50);

        // Assert
        assertThat(result.getQuantity()).isEqualTo(150);
        verify(productRepository).save(product);
    }

    @Test
    void updateStock_InsufficientStock_ThrowsValidationException() {
        // Arrange
        when(productRepository.findById(1L)).thenReturn(Optional.of(product));

        // Act & Assert
        assertThatThrownBy(() -> productService.updateStock(1L, -150))
            .isInstanceOf(ValidationException.class)
            .hasMessage("Insufficient stock");
    }

    @Test
    void updateStock_ProductNotFound_ThrowsResourceNotFoundException() {
        // Arrange
        when(productRepository.findById(1L)).thenReturn(Optional.empty());

        // Act & Assert
        assertThatThrownBy(() -> productService.updateStock(1L, 50))
            .isInstanceOf(ResourceNotFoundException.class)
            .hasMessage("Product not found");
    }
}
